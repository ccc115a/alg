# dgeom.sym 版的黎曼幾何與相對論測試
python -m tests.test_riemann
python -m tests.test_minkowski
python -m tests.test_schwarzschild_de_sitter
python -m tests.test_flrw_cosmology
python -m tests.test_mercury_precession
python -m tests.test_black_hole

# dgeom.sym 版的 dvector 測試
python -m tests.test_dvector

# dgeom.num 版的測試
python -m tests.test_num_dvector
