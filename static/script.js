document.getElementById('mine-btn').addEventListener('click', function() {
    fetch('/mine')
        .then(response => response.json())
        .then(data => {
            document.getElementById('mine-result').innerText = JSON.stringify(data, null, 4);
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

document.getElementById('transaction-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const sender = document.getElementById('sender').value;
    const recipient = document.getElementById('recipient').value;
    const amount = document.getElementById('amount').value;

    fetch('/transactions/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({sender, recipient, amount}),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('transaction-result').innerText = JSON.stringify(data, null, 4);
        document.getElementById('transaction-form').reset();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

document.getElementById('view-chain-btn').addEventListener('click', function() {
    fetch('/chain')
        .then(response => response.json())
        .then(data => {
            document.getElementById('chain-data').innerText = JSON.stringify(data, null, 4);
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
