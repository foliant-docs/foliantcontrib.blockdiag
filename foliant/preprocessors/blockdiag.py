'''`Blockdiag <http://blockdiag.com/>`__ preprocessor for Foliant documenation authoring tool.

Supports blockdiag, seqdiag, actdiag, and nwdiag.
'''

from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError
from typing import Dict
OptionValue = int or float or bool or str

from foliant.preprocessors.base import BasePreprocessor
from foliant.utils import output


class Preprocessor(BasePreprocessor):
    defaults = {
        'cache_dir': Path('.diagramscache'),
        'blockdiag_path': 'blockdiag',
        'seqdiag_path': 'seqdiag',
        'actdiag_path': 'actdiag',
        'nwdiag_path': 'nwdiag'
    }
    tags = 'blockdiag', 'seqdiag', 'actdiag', 'nwdiag'

    def _get_command(
            self,
            kind: str,
            options: Dict[str, OptionValue],
            diagram_src_path: Path
        ) -> str:
        '''Generate the image generation command. Options from the config definition are passed
        as command options (``cache_dir`` and ``*_path`` options are omitted).

        :param kind: Diagram kind: blockdiag, seqdiag, actdiag, or nwdiag
        :param options: Options extracted from the diagram definition
        :param diagram_src_path: Path to the diagram source file

        :returns: Complete image generation command
        '''

        components = [self.options[f'{kind}_path']]

        params = self.options.get('params', {})

        for option_name, option_value in {**params, **options}.items():
            if option_name == 'caption':
                continue

            elif option_value is True:
                components.append(f'--{option_name.replace("_", "-")}')

            elif option_name == 'format':
                components.append(f'-T {option_value}')

            else:
                components.append(f'--{option_name.replace("_", "-")}={option_value}')

        components.append(str(diagram_src_path))

        return ' '.join(components)

    def _process_diagram(self, kind: str, options: Dict[str, OptionValue], body: str) -> str:
        '''Save diagram body to .diag file, generate an image from it with the appropriate backend,
        and return the image ref.

        If the image for this diagram has already been generated, the existing version
        is used.

        :param kind: Diagram kind: blockdiag, seqdiag, actdiag, or nwdiag
        :param options: Options extracted from the diagram definition
        :param body: Diagram body

        :returns: Image ref
        '''

        self.logger.debug(f'Processing diagram: {kind}, {options}, {body}')

        body_hash = md5(f'{body}'.encode())
        body_hash.update(str(self.options).encode())

        diagram_src_path = self._cache_path / kind / f'{body_hash.hexdigest()}.diag'

        params = self.options.get('params', {})

        diagram_format = {**params, **options}.get('format', 'png')

        diagram_path = diagram_src_path.with_suffix(f'.{diagram_format}')

        img_ref = f'![{options.get("caption", "")}]({diagram_path.absolute().as_posix()})'

        if diagram_path.exists():
            self.logger.debug(f'Diagram found in cache: {diagram_path}.')
            self.logger.debug(f'Replacing diagram definition with {img_ref}.')
            return img_ref

        diagram_src_path.parent.mkdir(parents=True, exist_ok=True)

        with open(diagram_src_path, 'w', encoding='utf8') as diagram_src_file:
            diagram_src_file.write(body)

        self.logger.debug(f'Saved diagram source to {diagram_src_path}.')

        try:
            command = self._get_command(kind, options, diagram_src_path)

            self.logger.debug(f'Running the command: {command}')

            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

        except CalledProcessError as exception:
            self.logger.error(str(exception))

            if exception.output.decode().startswith('ERROR: '):
                error_message = f'Processing of diagram {diagram_src_path} failed: {exception.output.decode()}'

                output(error_message, self.quiet)

                self.logger.error(error_message)

            else:
                raise RuntimeError(f'Failed: {exception.output.decode()}')

        self.logger.debug(f'Replacing diagram definition with {img_ref}.')

        return img_ref

    def process_diagrams(self, content: str) -> str:
        '''Find diagram definitions and replace them with image refs.

        The definitions are fed to processors that convert them into images.

        :param content: Markdown content

        :returns: Markdown content with diagrams definitions replaced with image refs
        '''

        def _sub(diagram) -> str:
            return self._process_diagram(
                diagram.group('tag'),
                self.get_options(diagram.group('options')),
                diagram.group('body')
            )

        return self.pattern.sub(_sub, content)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache_path = self.project_path / self.options['cache_dir']

        self.logger = self.logger.getChild('blockdiag')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def apply(self):
        self.logger.info('Applying preprocessor.')

        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self.process_diagrams(content)

            if processed_content:
                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied.')
