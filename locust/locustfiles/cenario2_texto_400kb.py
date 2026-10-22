from locust import HttpUser, task, between

# Cenario 2: post de blog com um texto de aproximadamente 400KB
# POST_PATH e substituido automaticamente pelo scripts/setup_wordpress_content.sh
# apos a criacao do post no WordPress.
POST_PATH = "/?p=7"


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def abrir_post_texto_400kb(self):
        self.client.get(POST_PATH, name="cenario2_texto_400kb")
