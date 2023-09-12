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
  
    // Listen for the submit button click
    document.querySelector("#submit-button").addEventListener("click", function () {
      // Send the changedRows array to the Flask server using a GET request
      const queryParams = new URLSearchParams(changedRows.map(row => `row_${row.rowId}=${row.value}`));
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
    });
  });