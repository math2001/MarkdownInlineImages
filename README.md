# MarkdownInlineImages

MarkdownInlineImages is a plugin that renders your images below their link. Why? Because markdown
is just great, except for images. Reading a markdown file is really easy, almost as easy as a it can
be once it's converted to HTML for example, if you have a good color scheme. Except for images. This
plugin just completes this gap :smile:

![MarkdownInlineImages](screenshots/2-images.png)

So, to use it, just press <kbd>alt+i</kbd>, or, from the command palette, select
`MarkdownInlineImages: Render Images`. All the images will rendered.

#### Understanding the *actual* behaviour

When you press <kbd>alt+i</kbd>, the image are rendered, *except* if you haven't made **any** change
to the buffer, it'll hide all of them. So, if you want to hide the images, just press twice
<kbd>alt+i</kbd>.

## Which images can I load?

You can use images loaded from internet, or relative to your *file*. The support formats are:

- `PNG`
- `BMP`
- `JPG`
- `GIF`

**Note**: *Every* images rendered is cached in a single file. Even the local ones.
