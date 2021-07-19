'use strict';

const mediaStreamConstraints = {
  video: true
}

//Video Related ELements
const localVideo = document.getElementById('localVideo');
const startButton = document.getElementById('startButton');
const endButton = document.getElementById('endButton');
let localStream;

const streamMessage = document.getElementById('stream-message');
localVideo.style.display = "None";
endButton.disabled = true;

streamMessage.innerHTML = "Waiting for stream to start...";


//Function for starting stream
function getLocalStream(mediaStream){
  localStream = mediaStream;
  localVideo.srcObject = mediaStream;
}

function handleSetMediaError(error){
  console.log("Set Media Error: " + error);
}

function startStream() {
  streamMessage.innerHTML = "You are streaming right now.";
  navigator.mediaDevices.getUserMedia(mediaStreamConstraints).then(getLocalStream).catch(handleSetMediaError);

  startButton.disabled = true;
  endButton.disabled = false;
  localVideo.style.display = "block";
}

function endStream(){
  endButton.disabled = true;
  startButton.disabled = false;

  const video = localVideo.srcObject;
  const videoTrack = video.getTracks();

  videoTrack.forEach(function(track) {
      track.stop();
  });

  video.srcObject = null;
  localVideo.style.display = "None";
  streamMessage.innerHTML = "The stream has ended.";
}

//Add button behavior
startButton.addEventListener('click', startStream);
endButton.addEventListener('click', endStream);