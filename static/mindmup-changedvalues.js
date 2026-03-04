document.addEventListener("DOMContentLoaded", function () {
  const changedRows = [];

  // Add the editableTableWidget plugin to your table
  $('#mainTable').editableTableWidget();

  // Remove tabindex from delete cells and new player row cells so the
  // editable widget does not treat them as editable cells
  $('#mainTable .delete-cell-td, #mainTable tfoot td').prop('tabindex', -1);

  // Listen for the change event on table cells
  $('#mainTable').on('change', 'td', function () {
    const cell = $(this);
    const row = cell.closest('tr');
    const rowId = row.attr('data-row-id');
    const value = cell.text().trim(); // Get the edited cell value

    if (!rowId) return; // Skip tfoot rows (new player / delete cells)

    // Check if the row is already in the changedRows array
    const existingRow = changedRows.find(row => row.rowId === rowId);

    if (existingRow) {
      existingRow.value = value;
    } else {
      changedRows.push({ rowId, value });
    }
  });

  $('#mainTable td').on('validate', function() {
    // Skip cells in the new player row (tfoot)
    if ($(this).closest('tfoot').length > 0) return true;
    // Check if the cell belongs to the "names" column (e.g., assuming "names" is the first column)
    if ($(this).index() === 0) {
      window.alert("You cannot edit the 'names' column.");
      return false; // Mark cell as invalid
    }
    // Check if the cell belongs to the "total" column (e.g., assuming "total" is the second column)
    if ($(this).index() === 1) {
      const newValue = parseFloat($(this).text().trim());
      if (isNaN(newValue) || newValue < 0 || newValue > 100) {
        window.alert("Please enter a valid number between 0 and 100 in the 'total' column.");
        return false; // Mark cell as invalid
      }
    }
  });

  // New player name input: clear placeholder on focus, restore on blur
  const newPlayerNameInput = document.getElementById('newPlayerName');
  if (newPlayerNameInput) {
    newPlayerNameInput.addEventListener('focus', function () {
      if (this.value === 'NewPlayer') this.value = '';
    });
    newPlayerNameInput.addEventListener('blur', function () {
      if (this.value.trim() === '') this.value = 'NewPlayer';
    });
  }

  // Listen for the submit button click
  document.querySelector("#submit-button").addEventListener("click", function () {
    // Build query params from changed existing-player rows
    const queryParams = new URLSearchParams(changedRows.map(row =>
      [`row_${row.rowId}`, row.value]
    ));

    // Check for a new player entered in the inline input row
    const newPlayerTotal = document.getElementById('newPlayerTotal');
    const newName = newPlayerNameInput ? newPlayerNameInput.value.trim() : '';
    const newTotal = newPlayerTotal ? newPlayerTotal.value.trim() : '77';

    if (newName && newName !== 'NewPlayer') {
      queryParams.set('new_player', newName);
      if (newTotal && newTotal !== '77') {
        queryParams.set('new_player_total', newTotal);
      }
    }

    // Nothing to submit
    if (queryParams.toString() === '') {
      console.log("No changes to submit.");
      return;
    }

    // Send the data to the Flask server using a GET request
    try {
      const url = `/player?${queryParams.toString()}`;

      // Print the URL to the console for debugging
      console.log("URL to be sent:", url);

      window.location.href = url;
    } catch (error) {
      console.error("Error constructing URLSearchParams:", error);
    }
  });
});