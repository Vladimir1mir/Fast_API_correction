import requests

BASE_URL = "http://127.0.0.1:8080"


def print_response(response: requests.Response) -> None:
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    # Docker default port is 8080. For local uvicorn startup use http://127.0.0.1:8000.

    # Create advertisement
    # response = requests.post(
    #     f"{BASE_URL}/advertisement",
    #     json={
    #         "title": "advertisement_1",
    #         "description": "text of description 1",
    #         "price": 100,
    #         "author": "Petya Pypkin",
    #     },
    # )
    # print_response(response)

    # Update advertisement by id
    # response = requests.patch(
    #     f"{BASE_URL}/advertisement/1",
    #     json={
    #         "title": "advertisement_123",
    #         "price": 200,
    #     },
    # )
    # print_response(response)

    # Delete advertisement by id
    # response = requests.delete(f"{BASE_URL}/advertisement/1")
    # print_response(response)

    # Get advertisement by id
    # response = requests.get(f"{BASE_URL}/advertisement/1")
    # print_response(response)

    # Search advertisements by one or more fields
    # response = requests.get(
    #     f"{BASE_URL}/advertisement",
    #     params={
    #         "title": "advertisement",
    #         "author": "Petya",
    #         "price_min": 50,
    #         "price_max": 250,
    #     },
    # )
    # print_response(response)

    # Invalid create example, expected status 422
    # response = requests.post(
    #     f"{BASE_URL}/advertisement",
    #     json={
    #         "title": "",
    #         "description": "text of description 1",
    #         "price": -1,
    #         "author": "Petya Pypkin",
    #     },
    # )
    # print_response(response)
    pass
