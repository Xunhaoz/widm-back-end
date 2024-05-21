import pytest
from app import create_app, db
import warnings

warnings.filterwarnings("ignore")


@pytest.fixture(scope='session')
def app():
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


class TestPaper:
    DATA = [
        {
            "paper_publish_year": 2024,
            "paper_title": "paper_title_2024",
            "paper_origin": "paper_origin_2024",
            "paper_link": "paper_link_2024",
        },
        {
            "paper_publish_year": 2023,
            "paper_title": "paper_title_2023",
            "paper_origin": "paper_origin_2023",
            "paper_link": "paper_link_2023",
        }
    ]

    BASE_COL = ['id', 'create_time', 'update_time']

    def test_post_paper(self, client):
        for data in self.DATA:
            # testing route
            response = client.post("/paper", data=data)
            assert response.status_code == 200

            # testing data
            res_data = response.json['response']
            for col in self.BASE_COL:
                assert col in res_data
                del res_data[col]
            assert res_data == data

    def test_get_paper(self, client):
        # testing route
        response = client.get(f"/paper")
        assert response.status_code == 200

        res_datas = response.json['response']

        for data, res_data in zip(self.DATA, res_datas):
            # testing data
            for col in self.BASE_COL:
                assert col in res_data
                del res_data[col]
            assert res_data == data
