var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Red', 'Blue', 'Yellow'],
        datasets: [{
            data: [12, 19, 3],
            backgroundColor: [
                'red',
                'blue',
                'yellow'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
