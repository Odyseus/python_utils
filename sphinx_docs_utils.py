# -*- coding: utf-8 -*-
"""Utilities to generate documentations with Sphinx.
"""
import os

from runpy import run_path
from shutil import rmtree
from sphinx.cmd.build import main as sphinx_main

from . import exceptions
from . import file_utils
from . import shell_utils
from . import tqdm_wget
from .misc_utils import get_system_tempdir


def check_inventories_existence(update_inventories=False,
                                docs_sources_path="",
                                logger=None):
    """Check inventories existence. Download them if they don't exist.

    These inventory files are the ones used by the intersphinx Sphinx extension. Since
    I couldn't make the intersphinx_mapping option to download the inventory files
    automatically, I simply cut to the chase and did it myself.

    Parameters
    ----------
    update_inventories : bool
        Whether to force the update of the inventory files. Inventory files will be updated
        anyway f they don't exist.
    docs_sources_path : str, optional
        Path to the documentation source files that will be used to store the
        downloaded inventories.
    logger : LogSystem
        The logger.

    Raises
    ------
    exceptions.KeyboardInterruption
        Halt execution on Ctrl + C press.
    """
    logger.info(shell_utils.get_cli_separator("-"), date=False)
    logger.info("**Handling inventory files...**")
    mapping_file_path = os.path.join(docs_sources_path, "intersphinx_mapping.py")

    if file_utils.is_real_file(mapping_file_path):
        intersphinx_mapping = run_path(mapping_file_path)["intersphinx_mapping"]

        logger.info("**Checking existence of inventory files...**")

        for url, inv in intersphinx_mapping.values():
            inv_url = url + "/objects.inv"
            inv_path = os.path.join(docs_sources_path, inv)

            if update_inventories or not os.path.exists(inv_path):
                os.makedirs(os.path.dirname(inv_path), exist_ok=True)
                logger.info("**Downloading inventory file...**")
                logger.info("**Download URL:**")
                logger.info(inv_url, date=False)
                logger.info("**Download location:**")
                logger.info(inv_path, date=False)

                try:
                    tqdm_wget.download(inv_url, inv_path)
                except (KeyboardInterrupt, SystemExit):
                    raise exceptions.KeyboardInterruption()
                except Exception as err:
                    logger.error(err)
            else:
                logger.info("**Inventory file exists:**")
                logger.info(inv_path, date=False)


def generate_docs(root_folder="",
                  docs_src_path_rel_to_root="",
                  docs_dest_path_rel_to_root="docs",
                  apidoc_paths_rel_to_root=[],
                  doctree_temp_location_rel_to_sys_temp="",
                  ignored_modules=[],
                  generate_html=True,
                  generate_api_docs=False,
                  update_inventories=False,
                  force_clean_build=False,
                  build_coverage=True,
                  build_doctest=False,
                  logger=None):
    """Build this application documentation.

    Parameters
    ----------
    root_folder : str, optional
        Path to the main folder that most paths should be relative to.
    docs_src_path_rel_to_root : str, optional
        Docs sources path relative to root_folder.
    docs_dest_path_rel_to_root : str, optional
        Built docs destination path relative to root_folder.
    apidoc_paths_rel_to_root : list, optional
        A list of tuples. Each tuple of length two contains the path to the Python modules
        folder at index zero from which to extract docstrings and the path to where to store
        the generated rst files at index one.
    doctree_temp_location_rel_to_sys_temp : str, optional
        Name of a temporary folder that will be used to create a path relative to the
        system temporary folder.
    ignored_modules : list, optional
        A list of paths to Python modules relative to the root_folder. These are ignored
        modules whose docstrings are a mess and/or are incomplete. Because such docstrings
        will produce hundreds of annoying Sphinx warnings.
    generate_html : bool, optional
        Generate HTML.
    generate_api_docs : bool
        If False, do not extract docstrings from Python modules.
    update_inventories : bool, optional
        Whether to force the update of the inventory files. Inventory files will be updated
        anyway f they don't exist.
    force_clean_build : bool, optional
        Remove destination and doctrees directories before building the documentation.
    build_coverage : bool, optional
        If True, run :py:mod:`doctest` tests.
    build_doctest : bool, optional
        If True, build Sphinx coverage documents.
    logger : LogSystem
        The logger.
    """
    doctree_temp_location = os.path.join(get_system_tempdir(),
                                         doctree_temp_location_rel_to_sys_temp)
    docs_sources_path = os.path.join(root_folder, docs_src_path_rel_to_root)
    docs_destination_path = os.path.join(root_folder, docs_dest_path_rel_to_root)

    check_inventories_existence(update_inventories, docs_sources_path, logger)

    if generate_api_docs:
        logger.info(shell_utils.get_cli_separator("-"), date=False)
        logger.info("**Generating automodule directives...**")

        # NOTE: Force to create ``.. auto*`` directives with only the :members: option set.
        # This way I can set all autodoc options in conf.py file > autodoc_default_options.
        os.environ["SPHINX_APIDOC_OPTIONS"] = "members"
        from sphinx.ext.apidoc import main as apidoc_main

        # NOTE: Do not add more arguments to control ``.. auto*`` directives.
        # Set all autodoc options in conf.py file > autodoc_default_options.
        commmon_args = ["--module-first", "--separate", "--private",
                        "--force", "--suffix", "rst", "--output-dir"]

        for rel_source_path, rel_destination_path in apidoc_paths_rel_to_root:
            apidoc_destination_path = os.path.join(root_folder, rel_destination_path)

            if force_clean_build:
                rmtree(apidoc_destination_path, ignore_errors=True)

            apidoc_main(argv=commmon_args + [
                apidoc_destination_path,
                os.path.join(root_folder, rel_source_path)
            ] + ignored_modules)

    if build_coverage:
        logger.info(shell_utils.get_cli_separator("-"), date=False)
        logger.info("**Building coverage data...**")

        if force_clean_build:
            rmtree(doctree_temp_location, ignore_errors=True)

        sphinx_main(argv=[docs_sources_path, "-b", "coverage",
                          "-d", doctree_temp_location, os.path.join(docs_sources_path, "coverage")])

    if build_doctest:
        logger.info(shell_utils.get_cli_separator("-"), date=False)
        logger.info("**Building doctest tests...**")

        # NOTE: build_coverage already deleted and re-created temporary files.
        # Do not delete them; make use of them.
        if force_clean_build and not build_coverage:
            rmtree(doctree_temp_location, ignore_errors=True)

        sphinx_main(argv=[docs_sources_path, "-b", "doctest",
                    "-d", doctree_temp_location, os.path.join(docs_sources_path, "doctest")])

    if generate_html:
        logger.info(shell_utils.get_cli_separator("-"), date=False)
        logger.info("**Generating HTML documentation...**")

        if force_clean_build:
            rmtree(docs_destination_path, ignore_errors=True)

            # NOTE: build_coverage or build_doctest already deleted and re-created temporary files.
            # Do not delete them; make use of them.
            if not build_coverage and not build_doctest:
                rmtree(doctree_temp_location, ignore_errors=True)

        sphinx_main(argv=[docs_sources_path, "-b", "html", "-d", doctree_temp_location,
                          docs_destination_path])


def generate_man_pages(root_folder="",
                       docs_src_path_rel_to_root="",
                       docs_dest_path_rel_to_root="",
                       doctree_temp_location_rel_to_sys_temp="",
                       logger=None):
    """Generate man pages.

    Parameters
    ----------
    root_folder : str, optional
        Path to the main folder that most paths should be relative to.
    docs_src_path_rel_to_root : str, optional
        Docs sources path relative to root_folder.
    docs_dest_path_rel_to_root : str, optional
        Built docs destination path relative to root_folder.
    doctree_temp_location_rel_to_sys_temp : str, optional
        Name of a temporary folder that will be used to create a path relative to the
        system temporary folder.
    logger : LogSystem
        The logger.
    """
    logger.info(shell_utils.get_cli_separator("-"), date=False)
    logger.info("**Generating manual pages...**")
    doctree_temp_location = os.path.join(get_system_tempdir(),
                                         doctree_temp_location_rel_to_sys_temp)
    docs_sources_path = os.path.join(root_folder, docs_src_path_rel_to_root)
    man_pages_destination_path = os.path.join(root_folder, docs_dest_path_rel_to_root)

    sphinx_main(argv=[docs_sources_path, "-b", "man", "-d", doctree_temp_location,
                      man_pages_destination_path])


if __name__ == "__main__":
    pass
