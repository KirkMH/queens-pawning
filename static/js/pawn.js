function calculateChange() {
  const totalDue = $("#amount").val();
  const tendered = $("#tendered").val();
  const discount = $("#discount").val();
  const change = tendered - totalDue - discount;
  $("#change").val(change.toFixed(2));
}
$("#tendered").on("keyup", calculateChange);
$("#discount").on("change", calculateChange);
