const calculate = () => {
  const principal = parseFloat($("#principal").val());
  const interestPlusPenalty = parseFloat($("#interestPlusPenalty").val());
  const receivable = parseFloat($("#receivable").val());
  const tendered = parseFloat($("#tendered").val());

  let discount = parseFloat($("#discount").val()) || 0;
  let partial = parseFloat($("#partial").val()) || 0;
  let serviceFee = parseFloat($("#serviceFee").val()) || 0;

  let toPay = 0;
  if ($("#btnRedeem").prop("checked")) {
    toPay = interestPlusPenalty - discount + principal;
  } else {
    toPay = interestPlusPenalty - discount + serviceFee + partial;
  }
  const change = tendered - toPay;

  $("#receivable").val(toPay.toFixed(2));
  $("#amtToPay").val(toPay);
  $("#change").val(change.toFixed(2));
};
calculate();
$("#tendered").on("keyup", calculate);
$("#partial").on("keyup", calculate);
$("#discount").on("change", calculate);

function validateForm() {
  const change = parseFloat($("#change").val());
  let err = "";
  if (change < 0)
    err = "Tendered amount must be greater than or equal to the receivable.";

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
  const max_discount = parseFloat($("#interestPlusPenalty").val());
  const discount = parseFloat($("#discount").val());

  if (discount > 0) {
    toastr.error("Discount was already granted.");
    return;
  }

  bootbox.prompt({
    title:
      "Enter the requested discount amount (max of interest plus penalty):",
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
                        calculate();
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

function toggleForm() {
  $(".partial-payment").toggle();
  calculate();
}

$("#btnRedeem").on("change", function () {
  toggleForm();
});

$("#btnRenew").on("change", function () {
  toggleForm();
});

toggleForm();
