def render_surface_html():
    return """
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { margin:0; font-family: Arial, sans-serif; }
            #priceBox {
                position: absolute;
                top: 10px;
                left: 10px;
                background: #fff;
                padding: 5px 10px;
                border-radius: 5px;
                box-shadow: 0 0 5px rgba(0,0,0,0.3);
                z-index: 10;
            }
            #chartContainer {
                position: relative;
                width: 100%;
                height: 90vh;
            }
            #sourceIndicator {
                position: absolute;
                top: 50px; /* below Plotly title */
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                align-items: center;
                background: #fff;
                padding: 4px 8px;
                border-radius: 5px;
                box-shadow: 0 0 5px rgba(0,0,0,0.3);
                font-weight: bold;
                z-index: 10;
            }
            #sourceIcon {
                display: inline-block;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: red;
                margin-right: 6px;
            }
        </style>
    </head>
    <body>
        <!-- Price hover box -->
        <div id="priceBox">Hover to see price</div>

        <!-- Chart container with surface and traffic light -->
        <div id="chartContainer">
            <div id="sourceIndicator">
                <span id="sourceIcon" title="Pricing source status"></span>
                <span id="sourceText">Local</span>
            </div>
            <div id="surface" style="width:100%; height:100%;"></div>
        </div>

        <script>
        const priceDiv = document.getElementById('priceBox');
        const icon = document.getElementById('sourceIcon');
        const text = document.getElementById('sourceText');
        const plotDiv = document.getElementById('surface');

        fetch('/surface')
          .then(resp => resp.json())
          .then(data => {
            const fig = {
              data: [{
                x: data.strikes,
                y: data.tenors,
                z: data.vols,
                type: 'surface',
                colorscale: 'Viridis',
                hovertemplate:
                  'Strike: %{x:.2f}<br>' +
                  'Expiry: %{y:.2f} yrs<br>' +
                  'Implied Vol: %{z:.4f}<extra></extra>'
              }],
              layout: {
                title: { text: 'Implied Volatility Surface', x:0.5, xanchor:'center' },
                scene: {
                  xaxis: { title: 'Strike (K/S₀)' },
                  yaxis: { title: 'Expiry (Years)' },
                  zaxis: { title: 'Implied Volatility' }
                },
                margin: { l:20, r:20, b:20, t:70 }, // slightly taller top margin
                autosize: true
              }
            };
            Plotly.newPlot(plotDiv, fig.data, fig.layout);

            // Hover handler for live pricing
            plotDiv.on('plotly_hover', async function(eventData) {
                const x = eventData.points[0].x;
                const y = eventData.points[0].y;
                try {
                    const resp = await fetch(`/price?strike=${x}&expiry=${y}`);
                    const data = await resp.json();
                    priceDiv.innerHTML = `Strike: ${x.toFixed(3)} | Tenor: ${y.toFixed(3)} → Price: ${data.price.toFixed(4)}`;

                    if (data.source.startsWith('cpp')) {
                        icon.style.backgroundColor = 'green';
                        icon.title = 'Price sourced from C++ pricer';
                        text.innerText = 'Source: cpp_pricer';
                    } else {
                        icon.style.backgroundColor = 'red';
                        icon.title = 'Price sourced from local fallback';
                        text.innerText = 'Source: Local';
                    }
                } catch {
                    const price = (100 * Math.exp(-0.05 * y) * x).toFixed(4);
                    priceDiv.innerHTML = `Strike: ${x.toFixed(3)} | Tenor: ${y.toFixed(3)} → Price: ${price}`;
                    icon.style.backgroundColor = 'red';
                    icon.title = 'Price sourced from local fallback';
                    text.innerText = 'Local';
                }
            });

            plotDiv.on('plotly_unhover', () => {
                priceDiv.innerHTML = 'Hover to see price';
                icon.style.backgroundColor = 'grey';
                icon.title = 'Pricing source status';
                text.innerText = '?';
            });

            window.addEventListener('resize', () => Plotly.Plots.resize(plotDiv));
          });
        </script>
    </body>
    </html>
    """