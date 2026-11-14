"""Host metadata and artifact boundary for the independent GitHub Pages site."""
import copy
import publication_manifest as manifest


def hosting_configuration(config, profile):
    manifest.keys(profile, 'version platform canonical_url')
    owner, repository = config['repository'].split('/')
    expected = f'https://{owner.lower()}.github.io/{repository}/'
    if profile['version'] != 1 or profile['platform'] != 'github-pages' or profile['canonical_url'] != expected:
        raise ValueError('Pages must use the default repository URL, without a custom domain')
    hosted = copy.deepcopy(config)
    hosted['canonical_url'] = profile['canonical_url']
    return manifest.validate(hosted)


def prepare_artifact(staging, mount):
    root = staging / 'deployment/static' / mount.lstrip('/')
    if not (root / 'index.html').is_file():
        raise ValueError('Pages artifact has no site index')
    if (root / 'CNAME').exists():
        raise ValueError('the independent Pages publication must not contain CNAME')
    (root / '.nojekyll').touch()
    return root
