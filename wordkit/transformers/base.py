"""Base classes for transformers."""
import numpy as np

from itertools import chain
from sklearn.base import TransformerMixin


class BaseTransformer(TransformerMixin):
    """
    Base class for transformers without input features.

    Parameters
    ==========
    field : string
        The field to extract from the incoming dictionaries. For example, if
        you want to featurize orthographic forms, you can pass "orthography"
        to field. Most featurizers accept both "orthography" and "phonology"
        as possible fields.

    """

    def __init__(self, field):
        """Initialize the transformer."""
        self._is_fit = False
        self.features = None
        self.field = field

    def _check(self, x):
        """
        Check whether a feature string contains illegal features.

        Calculate the difference of the keys of the feature dict and x.
        Raises a ValueError if the result is non-empty.

        Parameters
        ==========
        x : string
            An input string.

        """
        x = set(chain.from_iterable(x))
        overlap = x.difference(set(self.features.keys()))
        if overlap:
            raise ValueError("The sequence contained illegal features: {0}"
                             .format(overlap))

    def inverse_transform(self, X):
        """Invert the transformation of a transformer."""
        raise NotImplementedError("Base class method.")

    def fit(self, X, y=None):
        """Fit the transformer."""
        return self

    def vectorize(self, x):
        """Vectorize a word."""
        raise NotImplementedError("Base class method.")

    def transform(self, words):
        """
        Transform a list of words.

        :param words: The list of words.
        """
        if not self._is_fit:
            raise ValueError("The transformer has not been fit yet.")
        total = np.zeros((len(words), self.vec_len))

        for idx, word in enumerate(words):
            x = self.vectorize(word)
            # This ensures that transformers which return sequences of
            # differing lengths still return non-jagged arrays.
            total[idx, :len(x)] = x

        return np.array(total)


class FeatureTransformer(BaseTransformer):
    """
    Base class for transformers which have features.

    Parameters
    ==========
    features : dict or tuple of dicts
        A key to array mapping, or a collection of key to array mappings.
    vec_len : int, optional, default 0
        The vector length.

    """

    def __init__(self, features, field, vec_len=0):
        """Wordkit transformer base class."""
        super().__init__(field)
        try:
            self.features = {k: np.array(v) for k, v in features.items()}
            self.dlen = max([len(x) for x in features.values()])
        except AttributeError:
            self.features = ({k: np.array(v) for k, v in features[0].items()},
                             {k: np.array(v) for k, v in features[1].items()})
        self.vec_len = vec_len