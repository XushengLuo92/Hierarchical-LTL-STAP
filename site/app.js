
(() => {
  const data = window.DEMOS;
  const video = document.getElementById('demo-video');
  const links = [...document.querySelectorAll('.case-link')];
  function select(id, updateURL) {
    const item = data.find(d => d.id === id) || data[0];
    video.pause();
    video.poster = item.poster;
    video.src = item.video;
    video.setAttribute('aria-label', item.label + ': ' + item.title);
    video.load();
    document.getElementById('selected-label').textContent = item.label;
    document.getElementById('selected-title').textContent = item.title;
    document.getElementById('selected-description').textContent = item.description;
    document.getElementById('video-label').textContent = item.label + ' / ' + item.robots + ' robots';
    document.getElementById('selected-meta').textContent = item.meta;
    document.getElementById('selected-note').textContent = item.note;
    const ul = document.getElementById('obligations');
    ul.replaceChildren(...item.obligations.map(text => {const li = document.createElement('li');li.textContent = text;return li;}));
    ['video', 'replay', 'validation'].forEach(kind => document.getElementById('download-' + kind).href = item[kind]);
    links.forEach(link => link.setAttribute('aria-current', String(Number(link.dataset.id) === item.id)));
    if (updateURL) {const url = new URL(location.href);url.searchParams.set('demo', item.id);history.replaceState(null, '', url);}
  }
  links.forEach(link => link.addEventListener('click', event => {if(event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)return;event.preventDefault();select(Number(link.dataset.id), true);}));
  const requested = Number(new URL(location.href).searchParams.get('demo'));
  if (data.some(item => item.id === requested)) select(requested, false);
  document.querySelectorAll('video').forEach(player => player.addEventListener('play', () => {document.querySelectorAll('video').forEach(other => {if(other !== player)other.pause();});}));
})();
