import unittest

from ..models import Project, Build, Deploy
from ..utils import sha1


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        """Set up the test case"""
        self.project = Project.create(name="kupy-test", org="owenstranathan",
                                      url="https://github.com/owenstranathan/kupy-test")
        self.project.secrets['SECRET_TOKEN'] = '12345'
        self.project.save()
        self.commit_id = "a29u9ufcuoi3u9r0aucisdjlk"
        self.build = Build.create(project_id=self.project.id, commit_id=self.commit_id, branch="develop")
        self.deploy = Deploy.create(project_id=self.project.id, build_id=self.build.id)

    def test_models(self) -> None:
        """Test that projects work"""
        full_name = "owenstranathan/kupy-test"
        self.assertEqual(full_name, self.project.full_name)
        self.assertEqual(sha1(full_name), self.project.id)
        self.assertEqual('12345', self.project.secrets['SECRET_TOKEN'])
        self.assertIn(self.build, list(self.project.builds))
        self.assertIn(self.deploy, list(self.project.deploys))

        build_id = sha1(f"{self.project.id}/{self.commit_id}")
        self.assertEqual(self.build.id, build_id)
        self.assertEqual(self.build.branch, "develop")
        self.assertEqual(self.build.commit_id, self.commit_id)
        self.assertEqual(self.build.project, self.project)
        self.assertIn(self.deploy, list(self.build.deploys))

        deploy_id = sha1(f"{self.project.id}/{self.build.id}")
        self.assertEqual(deploy_id, self.deploy.id)
        self.assertEqual(self.project, self.deploy.project)
        self.assertEqual(self.build, self.deploy.build)

    
    def tearDown(self) -> None:
        self.project.delete()
        self.build.delete()
        self.deploy.delete()


class TestBuild(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_build(self) -> None:
        pass
    
    def tearDown(self) -> None:
        pass


class TestDeploy(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_build(self) -> None:
        pass
    
    def tearDown(self) -> None:
        pass
