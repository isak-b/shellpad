import os

from shellpad.utils import is_valid_dir, extract_variant_id, find_file_variants, is_valid_file

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_W_ORIG = os.path.join(TESTS_PATH, "files/with_original")
PATH_WO_ORIG = os.path.join(TESTS_PATH, "files/without_original")


class TestIsValidDir:
    def test_valid(self):
        assert is_valid_dir(TESTS_PATH, extensions=[".ext"]) is True
        assert is_valid_dir(TESTS_PATH, extensions=[".aaa"]) is True
        assert is_valid_dir(TESTS_PATH, extensions=[".ext", ".nope"]) is True
        assert is_valid_dir(TESTS_PATH, extensions=[".ext", ".aaa"]) is True
        assert is_valid_dir(TESTS_PATH, extensions=[".aaa", ".nope"]) is True
        assert is_valid_dir(TESTS_PATH, extensions=[".ext", "aaa", ".nope"]) is True

    def test_invalid(self):
        assert is_valid_dir(TESTS_PATH, extensions=[".nope"]) is False


class TestExtractVariantId:
    def test_no_brackets(self):
        assert extract_variant_id("aaa.ext") == 0

    def test_brackets(self):
        assert extract_variant_id("aaa[1].ext") == 1
        assert extract_variant_id("aaa[2].ext") == 2

    def test_multiple_brackets(self):
        # NOTE: Should return the rightmost brackets
        assert extract_variant_id("aaa[1][2].ext") == 2

    def test_non_ids(self):
        # NOTE: Should not interpet non-int id as a variant id
        assert extract_variant_id("aaa[abc].ext") == 0


class TestFindFileVariants:
    def test_no_variants(self):
        path = os.path.join(PATH_W_ORIG, "aaa.ext")
        variants = find_file_variants(path, as_dict=False)
        assert isinstance(variants, list)
        assert len(variants) == 1
        assert variants[0] == path

    def test_variants_as_list_from_original(self):
        path = os.path.join(PATH_W_ORIG, "abc.ext")
        variants = find_file_variants(path, as_dict=False)
        assert isinstance(variants, list)
        assert len(variants) == 3
        assert variants[0] == os.path.join(PATH_W_ORIG, "abc.ext")
        assert variants[1] == os.path.join(PATH_W_ORIG, "abc[1].ext")
        assert variants[2] == os.path.join(PATH_W_ORIG, "abc[2].ext")

    def test_variants_as_list_from_copy(self):
        path = os.path.join(PATH_W_ORIG, "abc[1].ext")
        variants = find_file_variants(path, as_dict=False)
        assert isinstance(variants, list)
        assert len(variants) == 3
        assert variants[0] == os.path.join(PATH_W_ORIG, "abc.ext")
        assert variants[1] == os.path.join(PATH_W_ORIG, "abc[1].ext")
        assert variants[2] == os.path.join(PATH_W_ORIG, "abc[2].ext")

    def test_variants_as_dict_with_original(self):
        path = os.path.join(PATH_W_ORIG, "abc.ext")
        variants = find_file_variants(path, as_dict=True)
        assert isinstance(variants, dict)
        assert len(variants) == 3
        assert list(variants) == [0, 1, 2]
        assert variants[0] == os.path.join(PATH_W_ORIG, "abc.ext")
        assert variants[1] == os.path.join(PATH_W_ORIG, "abc[1].ext")
        assert variants[2] == os.path.join(PATH_W_ORIG, "abc[2].ext")

    def test_variants_as_dict_without_original(self):
        path = os.path.join(PATH_WO_ORIG, "abc.ext")
        variants = find_file_variants(path, as_dict=True)
        assert isinstance(variants, dict)
        assert len(variants) == 2
        assert list(variants) == [1, 2]
        assert variants[1] == os.path.join(PATH_WO_ORIG, "abc[1].ext")
        assert variants[2] == os.path.join(PATH_WO_ORIG, "abc[2].ext")


class TestIsValidFile:
    extensions = [".ext"]

    def test_invalid_ext(self):
        path = os.path.join(PATH_W_ORIG, "abc.txt")
        result = is_valid_file(path, extensions=self.extensions)
        assert result == False

    def test_valid_ext(self):
        path = os.path.join(PATH_W_ORIG, "abc.ext")
        result = is_valid_file(path, extensions=self.extensions)
        assert result == True

    def test_hide_file_variants_true_with_original_present(self):
        path = os.path.join(PATH_W_ORIG, "abc[1].ext")
        result = is_valid_file(path, extensions=self.extensions, hide_file_variants=True)
        assert result == False

    def test_hide_file_variants_false_with_original_present(self):
        path = os.path.join(PATH_W_ORIG, "abc[1].ext")
        result = is_valid_file(path, extensions=self.extensions, hide_file_variants=False)
        assert result == True

    def test_hide_file_variants_true_without_original_present(self):
        path = os.path.join(PATH_WO_ORIG, "abc[1].ext")
        result = is_valid_file(path, extensions=self.extensions, hide_file_variants=True)
        assert result == True

    def test_hide_file_variants_true_with_earlier_copy_present(self):
        path = os.path.join(PATH_W_ORIG, "abc[2].ext")
        result = is_valid_file(path, extensions=self.extensions, hide_file_variants=True)
        assert result == False

    def test_hide_file_variants_false_with_earlier_copy_present(self):
        path = os.path.join(PATH_W_ORIG, "abc[2].ext")
        result = is_valid_file(path, extensions=self.extensions, hide_file_variants=False)
        assert result == True
