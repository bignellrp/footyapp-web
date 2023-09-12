document.addEventListener("DOMContentLoaded", function () {
  const changedRows = [];

  // Add the editableTableWidget plugin to your table
  $('#mainTable').editableTableWidget();

  // Listen for the change event on table cells
  $('#mainTable').on('change', 'td', function () {
    const cell = $(this);
    const row = cell.closest('tr');
    const rowId = row.attr('data-row-id');
    const value = cell.text().trim(); // Get the edited cell value

    // Check if the row is already in the changedRows array
    const existingRow = changedRows.find(row => row.rowId === rowId);

    if (existingRow) {
      existingRow.value = value;
    } else {
      changedRows.push({ rowId, value });
    }
  });

  $('#mainTable td').on('validate', function() {
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

  // Listen for the submit button click
  document.querySelector("#submit-button").addEventListener("click", function () {
    // Check if the changedRows array is empty
    if (changedRows.length === 0) {
      console.log("No changes to submit.");
      return;
    }

    // Send the changedRows array to the Flask server using a GET request
    try {
      const queryParams = new URLSearchParams(changedRows.map(row =>
        [`row_${row.rowId}`, row.value]
      ));
      const url = `/player?${queryParams.toString()}`;

      // Print the URL to the console for debugging
      console.log("URL to be sent:", url);

      // Redirect or use fetch to send the data to your Flask server
      window.location.href = url;
      // Alternatively, use fetch() to send the data asynchronously
      /*
      fetch(url, {
        method: "GET",
      })

      .then(response => {
        // Handle the response
      });
      */
    } catch (error) {
      console.error("Error constructing URLSearchParams:", error);
    }
  });
});