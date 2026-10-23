from locust import HttpUser, task, between

# Cenario 5: busca no site (/?s=termo), uma das operacoes mais pesadas no
# banco de dados do WordPress por nao ser cacheada por padrao.
SEARCH_PATH = "/?s=cenario"


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def buscar(self):
        # timeout evita que uma requisicao travada sob carga extrema
        # fique pendurada indefinidamente e congele o teste inteiro.
        self.client.get(SEARCH_PATH, name="cenario5_busca", timeout=10)
