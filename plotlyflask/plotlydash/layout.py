"""Plotly Dash HTML layout override."""

html_layout = '''
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body class="dash-template">
            <header>
              <div class="nav-wrapper">
                  <div id="container" style="white-space:nowrap">

                        <div id="image" style="display:inline;">
                            <img src="/static/img/logo.png" class = "logo" height = "70"/>
                        </div>

                        <div id="texts" style="display:inline; white-space:nowrap;"> 
                            We are your savings hedgehog
                        </div>

                    </div>
                <nav>
                </nav>
            </div>
            </header>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
'''
