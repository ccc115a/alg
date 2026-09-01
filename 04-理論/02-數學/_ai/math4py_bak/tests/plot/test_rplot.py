"""Tests for plot/rplot.py - R-style plotting functions."""

import pytest
import numpy as np
from math4py.plot import pdf, dev_off
from math4py.plot.rplot import plot, hist, boxplot, qqnorm
from math4py.plot.rplot_entropy import plot_entropy, plot_kl


class TestPlot:
    def test_plot_scatter(self):
        """Test scatter plot (type='p')."""
        pdf("test_plot_scatter.pdf")
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        plot(x, y, type="p", main="Test Scatter")
        dev_off()

    def test_plot_line(self):
        """Test line plot (type='l')."""
        pdf("test_plot_line.pdf")
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)
        plot(x, y, type="l", main="Sine Wave")
        dev_off()

    def test_plot_both(self):
        """Test both points and lines (type='b')."""
        pdf("test_plot_both.pdf")
        x = np.array([0, 1, 2, 3])
        y = np.array([0, 1, 4, 9])
        plot(x, y, type="b", main="Points and Lines")
        dev_off()

    def test_plot_series(self):
        """Test time series plot (y only)."""
        pdf("test_plot_series.pdf")
        y = np.array([1, 3, 2, 5, 4])
        plot(y, main="Time Series")
        dev_off()


class TestHist:
    def test_hist_basic(self):
        """Test basic histogram."""
        pdf("test_hist_basic.pdf")
        data = np.random.normal(0, 1, 1000)
        hist(data, breaks=20, main="Normal Distribution")
        dev_off()

    def test_hist_density(self):
        """Test density histogram."""
        pdf("test_hist_density.pdf")
        data = np.random.exponential(1, 500)
        hist(data, breaks=15, freq=False, main="Exponential (Density)")
        dev_off()


class TestBoxplot:
    def test_boxplot_single(self):
        """Test single boxplot."""
        pdf("test_boxplot_single.pdf")
        data = np.random.normal(0, 1, 100)
        boxplot(data, main="Single Boxplot")
        dev_off()

    def test_boxplot_multiple(self):
        """Test multiple boxplots."""
        pdf("test_boxplot_multiple.pdf")
        g1 = np.random.normal(0, 1, 50)
        g2 = np.random.normal(2, 1.5, 50)
        boxplot(g1, g2, names=["Group A", "Group B"], main="Comparison")
        dev_off()


class TestQQNorm:
    def test_qqnorm_normal(self):
        """Q-Q plot of normal data should be roughly linear."""
        pdf("test_qqnorm_normal.pdf")
        data = np.random.normal(0, 1, 200)
        qqnorm(data, main="Q-Q Plot: Normal Data")
        dev_off()

    def test_qqnorm_uniform(self):
        """Q-Q plot of uniform data should deviate from line."""
        pdf("test_qqnorm_uniform.pdf")
        data = np.random.uniform(0, 1, 100)
        qqnorm(data, main="Q-Q Plot: Uniform Data")
        dev_off()


class TestPlotEntropy:
    def test_plot_entropy_uniform(self):
        """Plot entropy of uniform distribution."""
        pdf("test_entropy_uniform.pdf")
        p = np.array([0.25, 0.25, 0.25, 0.25])
        plot_entropy(p, main="Uniform Distribution Entropy")
        dev_off()

    def test_plot_entropy_certain(self):
        """Plot entropy of certain event."""
        pdf("test_entropy_certain.pdf")
        p = np.array([1.0, 0.0, 0.0])
        plot_entropy(p, main="Certain Event")
        dev_off()


class TestPlotKL:
    def test_plot_kl_identical(self):
        """KL divergence of identical distributions."""
        pdf("test_kl_identical.pdf")
        p = np.array([0.5, 0.5])
        q = np.array([0.5, 0.5])
        plot_kl(p, q, main="KL(P||Q) = 0")
        dev_off()

    def test_plot_kl_different(self):
        """KL divergence of different distributions."""
        pdf("test_kl_different.pdf")
        p = np.array([0.5, 0.5])
        q = np.array([0.8, 0.2])
        plot_kl(p, q, main="KL(P||Q) > 0")
        dev_off()