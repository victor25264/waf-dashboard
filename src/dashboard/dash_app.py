from src.waf_data.waf_data_getter import WAFDataGetter
from datetime import datetime, timedelta
from dash import Dash, dcc, callback, Input, Output, html
import plotly.express as px
import dash_mantine_components as dmc

class DashAppFactory:
    """
    A factory class to create and manage multiple Dash applications
    within a single Flask server.
    """
    def __init__(self, flask_server, statics = None, health_checker = None, waf_getter=None):
        self.flask_server = flask_server
        self.statics = statics
        self.health_checker = health_checker
        self.waf_getter = waf_getter

    def __create_table(self, data):
        rows = [
            dmc.TableTr(
                [
                    dmc.TableTd(row["timestamp"]),
                    dmc.TableTd(row["rule_id"]),
                    dmc.TableTd(row["rule_name"]),
                    dmc.TableTd(row["src_ip"]),
                    dmc.TableTd(row["req_path"]),
                    dmc.TableTd(row["req_method"]),
                ]
            )
            for index, row in data.iterrows()
        ]

        head = dmc.TableThead(
            dmc.TableTr(
                [
                    dmc.TableTh("Timestampn"),
                    dmc.TableTh("Rule ID"),
                    dmc.TableTh("Rule Name"),
                    dmc.TableTh("Src IP"),
                    dmc.TableTh("Path"),
                    dmc.TableTh("Method"),
                ]
            )
        )
        body = dmc.TableTbody(rows)
        caption = dmc.TableCaption("Logs from the last 7 days")

        scroll_table = dmc.TableScrollContainer(
            dmc.Table([head, body, caption]),
            maxHeight=300,
            minWidth=600,
            type="scrollarea",
        )
        return scroll_table

    def __create_health_check(self):
        healthy = self.health_checker.is_service_healthy()
        color = "green" if healthy else "red"
        return dmc.Badge("Healthy" if healthy else "Unhealthy", color=color, variant="filled", id='live-health-badge',)

    def create_dashboard_main(self):
        """Creates the first Dash application instance for '/dashboard/one/'."""

        week_ago = datetime.now() - timedelta(days=7)
        day_ago = datetime.now() - timedelta(days=1)
        waf_data = self.waf_getter.get_waf_data(start_time=week_ago.timestamp())


        dash_app_instance = Dash(
            __name__,
            server=self.flask_server,
            url_base_pathname='/dashboard/',
        )

        scroll_table = self.__create_table(waf_data)
        health_badge = self.__create_health_check()
        first_column= dmc.Container([
                dmc.Title('Dashboard One - WAF Logs', size="h3" , order=1, mt="lg"),
                dmc.Grid(
                    children=[
                        dmc.GridCol([
                            html.Div(id='scroll-table-container', children=scroll_table),
                            
                        ], span=6),
                        dmc.GridCol(health_badge, span=6),
                        dcc.Interval(
                            id='interval-component',
                            interval=60*1000, 
                            n_intervals=3
                        )
                    ],
                ),

            ], fluid=True)

        dash_app_instance.layout = dmc.MantineProvider(
            dmc.Card(
                dmc.CardSection(first_column, p="md"),
            )
        )

        # Callbacks for interactivity based on https://stackoverflow.com/questions/65011519/update-data-table-live-python-dash
        # and https://dash.plotly.com/live-updates
        @dash_app_instance.callback(
            Output('scroll-table-container', 'children'), 
            Input('interval-component', 'n_intervals')
        )
        def update_table_data(n):
            week_ago = datetime.now() - timedelta(days=7)
            waf_data_updated = self.waf_getter.get_waf_data(start_time=week_ago.timestamp())
            return self.__create_table(waf_data_updated) 
        
        @dash_app_instance.callback(
            Output('live-health-badge', 'children'), 
            Output('live-health-badge', 'color'),   
            Input('interval-component', 'n_intervals')
        )
        def update_health_badge(n):
            healthy = self.health_checker.is_service_healthy() 
            new_text = "Healthy" if healthy else "Unhealthy"
            new_color = "green" if healthy else "red"
            return new_text, new_color

        return dash_app_instance
    

        