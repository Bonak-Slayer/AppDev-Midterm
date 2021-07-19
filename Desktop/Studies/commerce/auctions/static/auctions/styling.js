const stream_message = document.getElementById('stream-message');

window.onload = function() {
  window.setInterval(fadeout, 1000);
  window.setInterval(fadein, 2000);
}

function fadeout() {
  if(stream_message.innerHTML === "The stream has ended."){
      stream_message.style.opacity = '1';
  }
  else{
      stream_message.style.opacity = '0';
  }
}

function fadein() {
  if(stream_message.innerHTML === "The stream has ended."){
      stream_message.style.opacity = '1';
  }
  else{
      stream_message.style.opacity = '1';
  }
}

