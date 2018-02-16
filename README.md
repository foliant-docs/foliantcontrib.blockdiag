# Blockdiag Preprocessor for Foliant

[Blockdiag](http://blockdiag.com/) is a tool to generate diagrams from plain text. This preprocessor finds diagram definitions in the source and converts them into images on the fly during project build. It supports all Blockdiag flavors: blockdiag, seqdiag, actdiag, and nwdiag.


## Installation

```shell
$ pip install foliantcontrib.blockdiag
```


## Config

To enable the preprocessor, add `blockdiag` to `preprocessors` section in the project config:

```yaml
preprocessors:
  - blockdiag
```

The preprocessor has a number of options:

```yaml
preprocessors:
  - blockdiag:
      cache_dir: !path .diagramscache
      blockdiag_path: blockdiag
      seqdiag_path: seqdiag
      actdiag_path: actdiag
      nwdiag_path: nwdiag
      params:
        ...
```

`cache_dir`
:   Path to the directory with the generated diagrams. It can be a path relative to the project root or a global one; you can use `~/` shortcut.

    >   **Note**
    >
    >   To save time during build, only new and modified diagrams are rendered. The generated images are cached and reused in future builds.

`*_path`
:   Paths to the `blockdiag`, `seqdiag`, `actdiag`, and `nwdiag` binaries. By default, it is assumed that you have these commands in `PATH`, but if they're installed in a custom place, you can define it here.

`params`
:   Params passed to the image generation commands (`blockdiag`, `seqdiag`, etc.). Params should be defined by their long names, with dashes replaced with underscores (e.g. `--no-transparency` becomes `no_transparency`); also, `-T` param is called `format` for readability:

        preprocessors:
          - blockdiag:
              params:
                antialias: true
                font: !path Anonymous_pro.ttf

    To see the full list of params, run `blockdiag -h`.


## Usage

To insert a diagram definition in your Markdown source, enclose it between `<<blockdiag>...</blockdiag>`, `<<seqdiag>...</seqdiag>`, `<actdiag>...</actdiag>`, or `<nwdiag>...</nwdiag>` tags (indentation inside tags is optional):

```markdown
Here's a block diagram:

<<blockdiag>
  blockdiag {
    A -> B -> C -> D;
    A -> E -> F -> G;
  }
</blockdiag>

Here's a sequence diagram:

<<seqdiag>
  seqdiag {
    browser  -> webserver [label = "GET /index.html"];
    browser <-- webserver;
    browser  -> webserver [label = "POST /blog/comment"];
                webserver  -> database [label = "INSERT comment"];
                webserver <-- database;
    browser <-- webserver;
  }
</seqdiag>
```

To set a caption, use `caption` option:

```markdown
Diagram with a caption:

<<blockdiag caption="Sample diagram from the official site">
  blockdiag {
    A -> B -> C -> D;
    A -> E -> F -> G;
  }
</blockdiag>
```

You can override `params` values from the preprocessor config for each diagram:

```markdown
By default, diagrams are in png. But this diagram is in svg:

<<blockdiag caption="High-quality diagram" format="svg">
  blockdiag {
    A -> B -> C -> D;
    A -> E -> F -> G;
  }
</blockdiag>
```
