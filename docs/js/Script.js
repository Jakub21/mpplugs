var switcher;
var menu;
var fontSize = 1;

let onload = () => {
  switcher = new Switcher();
  $on($id('FontDecr'), 'click', (evt) => {changeFontSize(-.05);});
  $on($id('FontIncr'), 'click', (evt) => {changeFontSize(.05);});
  menu = $id('Menu');
  addSection('Index');

  addMenuLabel('Guides');
  for (var id of ['Installation', 'QuickIntro'])
    addSection(id);

  addMenuLabel('API');
  for (var id of ['Program', 'Compiler', 'Executor', 'Plugin'])
    addSection(id);
  var section = window.location.href.split('#')[1];
  switcher.goto((section == undefined) ? 'Index' : section);

  for (var element of $tag('a')) {
    if (element.className == '') element.target = '_blank';
    }
}

let addMenuLabel = (name) => {
  var label = $create('h3');
  label.innerText = name;
  menu.appendChild(label);
}

let addSection = (id) => {
  var button = $create('a');
  button.innerText = id;
  button.href = '#' + id;
  button.classList.add('switcherButton');
  $on(button, 'click', (evt) => { switcher.goto(id) });
  menu.appendChild(button);
  switcher.addSection(new Section(id, $id(id)));
}

let changeFontSize = (delta) => {
  fontSize += delta;
  document.body.style.fontSize = fontSize + 'em';
}
