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

  bootbox.prompt({
    title: "Enter the requested discount amount:",
    inputType: "number",
    step: 0.01,

    callback: function (result) {
      if (result == null) return;

      let dialog = bootbox.dialog({
        title: "Requesting discount",
        message:
          '<p><i class="fas fa-spin fa-spinner"></i>&nbsp;Please wait for approval...</p>',
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
