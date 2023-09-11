// Define an empty array to store changed values
var changedValues = [];

// Bind a change event handler to all table cells except the first column
$('table#mainTable td:not(:first-child)').on('change', function (evt) {
    var cell = $(this),
        row = cell.closest('tr'),
        name = row.find('td:first-child').text(), // Get the name from the first column
        total = cell.text(); // Get the new total from the changed cell

    // Create an object to store the name and total
    var changedEntry = {
        name: name,
        total: total
    };

    // Check if the entry is already in the array
    var existingIndex = -1;
    for (var i = 0; i < changedValues.length; i++) {
        if (changedValues[i].name === name) {
            existingIndex = i;
            break;
        }
    }

    // If the entry exists, update it; otherwise, add it to the array
    if (existingIndex !== -1) {
        changedValues[existingIndex] = changedEntry;
    } else {
        changedValues.push(changedEntry);
    }

    // For testing, you can log the updated array
    console.log(changedValues);
});