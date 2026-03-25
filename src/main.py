import logging
import tempfile
from collections import defaultdict
from pathlib import Path

import git
import sqlalchemy
import yaml

import config
import const

logging.basicConfig(level=config.log_level())


class RODict(dict):
    def __setitem__(self, key, value):
        raise RuntimeError('Modification is not supported')


class App:
    def __init__(self):
        logging.debug('__init__()')

        try:
            self._prepare()
            self._perform()
        except Exception as e:
            logging.error(e, exc_info=True)
        finally:
            self._cleanup()

    def _prepare(self):
        logging.debug('_prepare()')

        # Database engine
        self._engine = sqlalchemy.create_engine('postgresql://{}:{}@{}:{}/{}'.format(
            config.postgres_username(),
            config.postgres_password(),
            config.postgres_host(),
            config.postgres_port(),
            config.postgres_database()
        ))

        # Repository
        self._repo_dir = tempfile.TemporaryDirectory()
        self._repo = git.Repo.clone_from(config.git_private_repo_url(), self._repo_dir.name)

        # Students data
        self._students = RODict(yaml.safe_load(
            ((Path(self._repo_dir.name) / const.STUDENTS_FILE).read_text(encoding='utf-8'))
        ))

    def _perform(self):
        logging.debug('_perform()')

        # Fetch scores
        max_no, results = self._fetch()

        # Write to results.csv
        with open(Path(self._repo_dir.name) / const.RESULTS_FILE, 'w+', encoding='utf-8') as f:
            f.write('ФИО,Группа,{},Среднее\n'.format(','.join([f'ЛР{i + 1}' for i in range(max_no)])))
            for r in results:
                f.write('{},{},{},{}\n'.format(
                    r['name'],
                    r['group'],
                    ','.join([str(r['scores'][i + 1]) for i in range(max_no)]),
                    '{:.2f}'.format(r['avg'])
                ))

        # Commit
        actor = git.Actor(config.git_actor_name(), config.git_actor_email())
        self._repo.index.add([const.RESULTS_FILE])
        self._repo.index.commit(
            message=config.git_commit_message(),
            author=actor,
            committer=actor
        )
        self._repo.remote().push()

    def _cleanup(self):
        logging.debug('_cleanup()')

        # Release repo
        if getattr(self, '_repo', None) is not None:
            self._repo.close()

        # Remove repo temp dir
        if getattr(self, '_repo_dir', None) is not None:
            self._repo_dir.cleanup()

    def _fetch(self) -> tuple[int, list]:
        logging.debug('_fetch()')

        if len(self._students) == 0:
            return 0, []

        # Fetch scores
        max_no = 0
        scores = defaultdict(dict)
        with self._engine.connect() as con:
            res = con.execute(
                sqlalchemy.text('SELECT code, lab_no, score FROM alts_results WHERE code IN :codes'),
                {
                    'codes': tuple(self._students.keys())
                }
            )
        for row in res:
            max_no = max(max_no, row.lab_no)
            scores[row.code][row.lab_no] = row.score

        # Build results
        results = []
        for code, data in self._students.items():
            code_scores = scores.get(code, {})
            full_scores = {i: code_scores.get(i, 0) for i in range(1, max_no + 1)}
            results.append({
                'name': data['name'],
                'group': data['group'],
                'scores': full_scores,
                'avg': sum(full_scores.values()) / max_no if max_no > 0 else 0
            })

        # Sort and return
        return max_no, sorted(results, key=lambda x: (x['group'], x['name']))


if __name__ == '__main__':
    App()
