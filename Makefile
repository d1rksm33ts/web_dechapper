.PHONY: check test compose-test

check:
	python manage.py check
	python manage.py makemigrations --check --dry-run

test:
	DJANGO_DEBUG=true DJANGO_SECURE_COOKIES=false python manage.py test

compose-test:
	docker compose -f compose.test.yml up --build --abort-on-container-exit --exit-code-from test
	docker compose -f compose.test.yml down --volumes --remove-orphans

