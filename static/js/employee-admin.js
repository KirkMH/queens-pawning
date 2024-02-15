document.addEventListener("DOMContentLoaded", function () {
  var branchSelect = document.querySelector("#id_employee-0-branch");
  var userTypeSelect = document.querySelector("#id_employee-0-user_type");

  function updateUserTypeOptions() {
    while (userTypeSelect.firstChild) {
      userTypeSelect.firstChild.remove();
    }

    if (branchSelect.value) {
      userTypeSelect.add(new Option("Cashier", "1"));
    } else {
      userTypeSelect.add(new Option("Staff", "2"));
      userTypeSelect.add(new Option("Expense Personnel", "3"));
      userTypeSelect.add(new Option("Administrator", "4"));
    }
  }

  branchSelect.addEventListener("change", updateUserTypeOptions);
  updateUserTypeOptions();
});
