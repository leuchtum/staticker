var selected = [];

const Item = (name) => `
<li class="list-group-item" name="${name}">
<div class="d-flex justify-content-between">
<span>${name}</span>
    <button type="button" class="btn btn-danger delete"><span class="glyphicon  glyphicon-remove"></span>Delete</button>
</div>
</li>
`;


function sort_case_sensitive(array) {
    return array.sort(function (a, b) {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    }); 
}

function onSelectItem(item) {
    if (!selected.includes(item.label)) {
        selected.push(item.label);
        var todo = document.getElementById("players");
        selected = sort_case_sensitive(selected)
        todo.innerHTML = selected.map(Item).join("");
    }
    document.getElementById("playersearch").value = "";
}

$(document).ready(function () {
    $('#players').on('click', '.delete', function (e) {
        var elem = $(e.currentTarget).closest('li');
        var name = elem[0].attributes["name"].value;
        elem.remove();
        const index = selected.indexOf(name);
        if (index > -1) {
            selected.splice(index, 1);
        }
    });
});

$.getJSON("/data/player?load_all=1", function (data) {
    $('#playersearch').autocomplete({
        source: data,
        onSelectItem: onSelectItem,
        treshold: 1
    });
});


document.getElementById('form').addEventListener('submit', function(e) {
    var data = JSON.stringify(selected);
    document.getElementById("selected_players").value = data;
  });