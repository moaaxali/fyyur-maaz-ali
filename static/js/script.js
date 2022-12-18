window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

let delBtns = document.querySelectorAll('.del-venue')

console.log(delBtns)

for (let i = 0; i < delBtns.length; i++) {
  const deleteBtn = delBtns[i];
  deleteBtn.onclick = function (e) {
    console.log("Delete event: ", e);
    const venueId = e.target.dataset.id;
    fetch('/venues/' + venueId, {
      method: 'DELETE'
    }).then(function () {
      console.log('Parent?', e.target);
      window.location.reload()
    })
    .catch(function (e) {
      console.error(e);
    });
  };
}