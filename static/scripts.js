const socket = io();

if (typeof userId !== 'undefined') {
    socket.emit('join', { user_id: userId });
}

socket.on('receive_message', (data) => {
    const messageList = document.querySelector('.list-group');
    const newMessage = document.createElement('li');
    newMessage.classList.add('list-group-item');
    newMessage.innerHTML = `
        <h5>From: User ${data.sender_id}</h5>
        <p>${data.content}</p>
        <small class="text-muted">Just now</small>
    `;
    messageList.prepend(newMessage);
});

window.addEventListener('beforeunload', () => {
    if (typeof userId !== 'undefined') {
        socket.emit('leave', { user_id: userId });
    }
});

const darkModeToggle = document.getElementById('dark-mode-toggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
    });
}
