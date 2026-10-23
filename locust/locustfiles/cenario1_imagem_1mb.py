from locust import HttpUser, task, between

# Cenario 1: post de blog com uma imagem de aproximadamente 1MB
POST_PATH = "/?p=4"
IMAGE_PATH = "/wp-content/uploads/2026/10/imagem_1mb.jpg"


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def abrir_post_imagem_1mb(self):
        # timeout evita que uma requisicao travada sob carga extrema
        # fique pendurada indefinidamente e congele o teste inteiro.
        self.client.get(POST_PATH, name="cenario1_imagem_1mb_html", timeout=10)
        self.client.get(IMAGE_PATH, name="cenario1_imagem_1mb_imagem", timeout=10)
