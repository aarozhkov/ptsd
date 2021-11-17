import sys

if len(sys.argv) < 2:
    new_tag = '1.0.0'
    print(f'Latest was not found.')
else:
    latest_tag = sys.argv[1]
    print(f'Latest tag: {latest_tag}')

    semver = latest_tag.split('.')
    major = int(semver[0])
    minor = int(semver[1])
    patch = int(semver[2])

    patch += 1

    new_tag = f'{major}.{minor}.{patch}'

print(f'New tag: {new_tag}')

with open('tag.env', 'w') as f:
    f.write(f'NEW_TAG={new_tag}')
