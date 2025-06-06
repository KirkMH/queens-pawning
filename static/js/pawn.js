const calculate = async () => {
  const action = $("#action").val();
  const transaction_type = $("#transaction_type").val();
  console.log(`transaction_type: ${transaction_type}`);
  const principal = parseFloat($("#principal").val()) || 0;
  console.log(`principal: ${principal}`);
  const additionalPrincipal = parseFloat($("#additionalPrincipal").val()) || 0;
  console.log(`additionalPrincipal: ${additionalPrincipal}`);
  const interestPlusPenalty = parseFloat($("#interestPlusPenalty").val()) || 0;
  console.log(`interestPlusPenalty: ${interestPlusPenalty}`);
  const appraised_value = parseFloat($("#appraised_value").val()) || 0;
  console.log(`appraised_value: ${appraised_value}`);
  const tendered = parseFloat($("#tendered").val()) || 0;
  console.log(`tendered: ${tendered}`);
  const advIntUri = $("#advIntUri").val();
  console.log(`advIntUri: ${advIntUri}`);
  const promisedDate = $("#promised_renewal_date").val();
  console.log(`promisedDate: ${promisedDate}`);
  let date_granted = $("#date_granted").val();
  const renew_date = $("#renew").val();
  console.log(`date_granted: ${date_granted}`);
  console.log(`renew_date: ${renew_date}`);

  if (renew_date) date_granted = renew_date;

  let discount = parseFloat($("#discount").val()) || 0;
  console.log(`discount: ${discount}`);
  let partial = parseFloat($("#partial").val()) || 0;
  console.log(`partial: ${partial}`);
  let serviceFee = parseFloat($("#serviceFee").val()) || 0;
  console.log(`serviceFee: ${serviceFee}`);

  if (principal - partial + additionalPrincipal > appraised_value) {
    console.log("The total principal must not exceed the appraised value.");
    toastr.error("The total principal must not exceed the appraised value.");
    $("#additionalPrincipal").val("0.00");
    calculate();
    return;
  }

  let toPay = 0;
  if (action === "Redeem") {
    toPay = interestPlusPenalty - discount + principal;
  } else {
    toPay =
      interestPlusPenalty -
      discount +
      serviceFee +
      partial -
      additionalPrincipal;

    if (transaction_type === "NEW") {
      const newPrincipal = principal + additionalPrincipal - partial;
      const response = await fetch(
        advIntUri +
          "?principal=" +
          newPrincipal +
          "&promised_date=" +
          promisedDate +
          "&date_granted=" +
          date_granted
      );
      if (!response.ok) {
        $("#advanceInterest").val("0.00");
        console.log(`error: ${error}`);
      } else {
        const data = await response.json();
        console.log(`result: ${JSON.stringify(data)}`);
        const advInt = parseFloat(data["advance_interest"]);
        $("#advanceInterest").val(advInt.toFixed(2));
        toPay += advInt;
        showToPayAndChange(tendered, toPay);
      }
    }
  }
  showToPayAndChange(tendered, toPay);
};
$("#tendered").on("keyup", calculate);
$("#partial").on("keyup", calculate);
$("#discount").on("change", calculate);
$("#additionalPrincipal").on("keyup", calculate);
$("#promised_renewal_date").on("change", calculate);

function showToPayAndChange(tendered, toPay) {
  const change = tendered - toPay;

  $("#receivable").val(toPay.toFixed(2));
  $("#amtToPay").val(toPay);
  $("#change").val(change.toFixed(2));
}

function validateForm() {
  const change = parseFloat($("#change").val());
  const redeem = $("#btnRedeem").prop("checked");
  const renew = $("#btnRenew").prop("checked");
  const promisedDate = $("#promised_renewal_date").val();
  const transaction_type = $("#transaction_type").val();
  console.log(`Promised date: ${promisedDate}`);

  let err = "";
  if (change < 0)
    err = "Tendered amount must be greater than or equal to the receivable.";
  else if (renew && transaction_type === "NEW" && promisedDate === "")
    err = "Please enter the promised renewal date.";

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
  } else if (max_discount == 0) {
    toastr.warning(
      "There is no interest or penalty due where the discount will be applied to."
    );
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

//toggleForm();
