from locust import HttpUser, task, between

# Cenario 4: pagina inicial do blog, que lista varios posts de uma vez
# (consulta mais pesada ao banco de dados do que abrir um unico post).
HOME_PATH = "/"


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def abrir_home(self):
        # timeout evita que uma requisicao travada sob carga extrema
        # fique pendurada indefinidamente e congele o teste inteiro.
        self.client.get(HOME_PATH, name="cenario4_home", timeout=10)
