<!-- ═══════════════════════════════════════════════════════════════════════════
     build/CHEATSHEET.md
     ─────────────────────────────────────────────────────────────────────────
     Generated with the assistance of AI (Claude, Anthropic).

     Quick reference for Quarto syntax used in this book.
     ═══════════════════════════════════════════════════════════════════════════ -->

# Author cheatsheet

Quick reference for Quarto syntax used in this book. Keep this open while writing.

---

## Cross-references

```markdown
# My Section {#sec-my-section}        ← label a section
@sec-my-section                        ← reference it → "Section 2.1"

![Caption](fig.png){#fig-my-fig}       ← label a figure
@fig-my-fig                            ← reference it → "Figure 2.1"

| col | col |                          ← label a table
: Caption {#tbl-my-table}
@tbl-my-table                          ← "Table 2.1"

$$E = mc^2$$ {#eq-einstein}            ← label an equation
@eq-einstein                           ← "Equation 2.1"
```

---

## Code chunks

### Python

````markdown
```{python}
#| label: fig-scatter          ← required if referencing
#| fig-cap: "Caption text."    ← shown below figure
#| echo: true                  ← show source (default from _quarto.yml)
#| eval: true                  ← run the cell
#| warning: false              ← suppress warnings
#| cache: true                 ← cache this cell's output
```
````

### R

````markdown
```{r}
#| label: fig-histogram
#| fig-cap: "Caption text."
#| fig-width: 7
#| fig-height: 4
```
````

### Inline values

```markdown
The mean is `{python} round(x.mean(), 3)`.
The p-value is `{r} format(p, digits=3)`.
```

---

## Callout blocks

```markdown
::: {.callout-note}
## Optional title
Content.
:::

::: {.callout-tip collapse="true"}
Collapsed tip — good for solutions / extra detail.
:::

::: {.callout-warning}
Watch out for this.
:::

::: {.callout-important}
Do not skip this.
:::
```

---

## Figures

```markdown
![Caption text.](path/to/fig.png){#fig-id width=80%}

::: {#fig-side layout-ncol=2}
![Left.](a.png)
![Right.](b.png)
Two figures side by side.
:::
```

---

## Tables

```markdown
| Col A | Col B | Col C |
|-------|------:|------:|
| x     | 1.2   | 3.4   |
: Caption. {#tbl-id tbl-colwidths="[50,25,25]"}
```

---

## Parts & appendices (in `_quarto.yml`)

```yaml
chapters:
  - index.qmd
  - part: "Part I: Foundations"
    chapters:
      - chapters/ch01-.../index.qmd
  - part: "Part II: Applications"
    chapters:
      - chapters/ch03-.../index.qmd
appendices:
  - appendices/notation.qmd
```

---

## Margin notes

```markdown
[This appears in the margin.]{.aside}
```

---

## Theorems & proofs

```markdown
::: {#thm-name}
## Theorem title
Statement of theorem.
:::

::: {.proof}
Proof here.
:::
```

---

## Citations

```markdown
[@knuth1984]           → (Knuth, 1984)
[@knuth1984, p. 42]    → (Knuth, 1984, p. 42)
@knuth1984             → Knuth (1984)  [narrative form]
[-@knuth1984]          → (1984)        [suppress author]
```

Add entries to `references.bib`.

---

## Shortcodes

```markdown
{{< pagebreak >}}      ← force page break (PDF)
{{< include path.qmd >}} ← include another file inline
{{< video url >}}      ← embed video (HTML only)
```

---

## Freeze control

In `_quarto.yml`:
```yaml
execute:
  freeze: auto    # default — re-run only changed cells
```

Force re-run a single chapter:
```bash
quarto render chapters/ch01-introduction/index.qmd --no-freeze
```
