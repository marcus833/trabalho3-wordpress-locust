from locust import HttpUser, task, between

# Cenario 3: post de blog com uma imagem de aproximadamente 300KB
POST_PATH = "/?p=9"
IMAGE_PATH = "/wp-content/uploads/2026/10/imagem_300kb.jpg"


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def abrir_post_imagem_300kb(self):
        self.client.get(POST_PATH, name="cenario3_imagem_300kb_html")
        self.client.get(IMAGE_PATH, name="cenario3_imagem_300kb_imagem")
