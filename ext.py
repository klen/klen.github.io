from __future__ import with_statement

from pelican import Pelican, Writer


class KlenWritter(Writer):

    def write_feed(self, articles, *args, **kwargs):
        articles = filter(lambda a: a.category.name != 'Books', articles)
        return super(KlenWritter, self).write_feed(articles, *args, **kwargs)

    def write_file(self, name, template, context, relative_urls=True,
        paginated=None, **kwargs):

        context['dates'] = filter(
                lambda a: a.category.name != 'Books',
                context['dates']
        )
        category = kwargs.get('category')
        if category:
            categories = dict(context.get('categories', dict()))
            articles = categories[category]
            kwargs['catalog'] = context['CATALOG'][category]

        article = kwargs.get('article')
        if article and articles:
            for i in xrange(len(articles)):
                a = articles[i]
                if a.title == article.title:
                    kwargs['prev'] = articles[i - 1] if i > 0 else None
                    kwargs['next'] = articles[i + 1] if i < (len(articles) - 1) else None

        return super(KlenWritter, self).write_file(name, template, context,
                relative_urls=relative_urls, paginated=paginated, **kwargs)


class KlenPelican(Pelican):

    def get_writer(self):
        return KlenWritter(self.output_path, settings=self.settings)
