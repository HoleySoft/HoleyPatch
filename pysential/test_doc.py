# -*- coding: utf-8 -*-
import protodoc
import pysential


def main() -> None:
    docs = protodoc.AutoDoc()
    html_docs = protodoc.Document()

    docs.add_dir('./pysential')
    docs.add_dir('./pysential_test')
    # docs.add_document('./pysential/package_manager/imagemanager.py')
    # docs.add_document('./protodoc/autodoc.py')
    # docs.add_document('./protodoc/test.py')

    docs.extract()


    html_docs.html_doc(
        docs.package,
        template_dir='./protodoc/template/default',
        output_dir='./protodoc_build'
    )


if __name__ == '__main__':
    main()
