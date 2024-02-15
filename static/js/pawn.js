function calculateChange() {
  const totalDue = $("#amount").val();
  const tendered = $("#tendered").val();
  const discount = $("#discount").val();
  const change = tendered - totalDue - discount;
  $("#change").val(change.toFixed(2));
}
calculateChange();
$("#tendered").on("keyup", calculateChange);
$("#discount").on("change", calculateChange);

function validatePayment(e) {
  e.preventDefault();
  console.log("Validating payment form");

  const minPayment = $("#min_payment").val();
  const maxPayment = $("#max_payment").val();
  const toPay = $("#amount").val();
  const tendered = $("#tendered").val();
  let err = "";
  if (toPay < minPayment || toPay > maxPayment)
    err = "Amount must be between the minimum payment and the total due.";
  else if (tendered < toPay)
    err =
      "Tendered amount must be greater than or equal to the amount to be paid.";

  if (err) {
    toastr.error(err);
  } else {
    $(this).unbind("submit").submit();
  }
}
$("#payment-form").on("submit", validatePayment);
