const calculateChange = () => {
  const totalDue = parseFloat($("#amount").val());
  const tendered = parseFloat($("#tendered").val());
  let discount = parseFloat($("#discount").val());
  if (!discount) discount = 0;
  const receivable = totalDue - discount;
  const change = tendered - receivable;

  $("#discount").val(discount.toFixed(2));
  $("#receivable").val(receivable.toFixed(2));
  $("#change").val(change.toFixed(2));
};
calculateChange();
$("#tendered").on("keyup", calculateChange);
$("#amount").on("keyup", calculateChange);
$("#discount").on("change", calculateChange);

function validateForm() {
  const minPayment = parseFloat($("#min_payment").val());
  const maxPayment = parseFloat($("#max_payment").val());
  const toPay = parseFloat($("#amount").val());
  const change = parseFloat($("#change").val());
  let err = "";
  if (toPay < minPayment || toPay > maxPayment)
    err = "Amount must be between the minimum payment and the total due.";
  else if (change < 0)
    err =
      "Tendered amount must be greater than or equal to the amount to be paid.";

  if (err) {
    toastr.error(err);
  }
  return !err;
}

const errorProcessor = (error, dialog) => {
  dialog.find(".bootbox-body").html(`<p class="text-danger">${error}</p>`);
  dialog.find(".modal-footer").remove();
  setTimeout(() => {
    dialog.modal("hide");
  }, 1500);
};

$("#request-discount").on("click", function () {
  const pawn_id = $("#pawn_id").val();
  const max_discount = parseFloat($("#max_discount").val());
  const discount = parseFloat($("#discount").val());

  if (discount > 0) {
    toastr.error("Discount was already granted.");
    return;
  }

  bootbox.prompt({
    title: "Enter the requested discount amount (max of interest due):",
    inputType: "number",
    step: 0.01,
    min: 1,
    max: max_discount,

    callback: function (result) {
      if (result == null) return;
      else if (result > max_discount) {
        toastr.error("Requested discount must not exceed the interest due.");
        return;
      }

      let dialog = bootbox.dialog({
        title: "Requesting discount",
        message:
          '<p><i class="fas fa-spin fa-spinner"></i>&nbsp;Please wait for the approval...</p>',
        closeButton: false,
        buttons: {
          cancel: {
            label: "Cancel",
            className: "btn-danger",
            callback: function () {
              dialog.modal("hide");
            },
          },
        },
      });

      dialog.init(function () {
        $.ajax({
          url: `/pawn/discounts/${pawn_id}/request`,
          type: "GET",
          data: {
            amount: result,
            interest_due: max_discount,
          },
          success: function (data) {
            const success = data["success"];
            const error = data["error"];

            if (success) {
              // wait until the request is approved
              const interval = setInterval(() => {
                $.ajax({
                  url: `/pawn/discounts/${pawn_id}/status`,
                  type: "GET",
                  success: function (data) {
                    const status = data["status"];
                    if (status !== "PENDING") {
                      clearInterval(interval);
                      dialog.modal("hide");
                      if (status === "REJECTED") {
                        toastr.error("Discount request rejected.");
                      } else {
                        toastr.success("Discount request approved.");
                        $("#discount").val(result);
                        calculateChange();
                      }
                    }
                  },
                  error: function (xhr, status, error) {
                    errorProcessor(
                      "An error occurred while processing your request. Please try again later.",
                      dialog
                    );
                  },
                });
              }, 10000);
            } else {
              errorProcessor(error, dialog);
            }
          },
          error: function (xhr, status, error) {
            errorProcessor(
              "An error occurred while processing your request. Please try again later.",
              dialog
            );
          },
        });
      });
    },
  });
});

function toggleForm(action) {
  const hide = action === "redeem";
  $("#partial")
    .parent()
    .parent()
    .css("display", hide ? "none" : "block");
}

$("#btnRedeem").on("click", function () {
  console.log("Redeem button clicked");
  if ($("#btnRedeem").prop("checked")) {
    toggleForm("redeem");
  }
});

$("#btnRenew").on("click", function () {
  console.log("Renew button clicked");
  if ($("#btnRenew").prop("checked")) {
    toggleForm("renew");
  }
});

toggleForm("redeem");
