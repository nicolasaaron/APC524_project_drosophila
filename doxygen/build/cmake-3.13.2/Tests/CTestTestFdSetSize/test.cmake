cmake_minimum_required(VERSION 2.8.10)

# Settings:
set(CTEST_DASHBOARD_ROOT                "/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CTestTest")
set(CTEST_SITE                          "nat-oitwireless-inside-vapornet100-b-21211.Princeton.EDU")
set(CTEST_BUILD_NAME                    "CTestTest-Darwin-clang++-FdSetSize")

set(CTEST_SOURCE_DIRECTORY              "/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CTestTestFdSetSize")
set(CTEST_BINARY_DIRECTORY              "/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CTestTestFdSetSize")
set(CTEST_CVS_COMMAND                   "CVSCOMMAND-NOTFOUND")
set(CTEST_CMAKE_GENERATOR               "Unix Makefiles")
set(CTEST_CMAKE_GENERATOR_PLATFORM      "")
set(CTEST_CMAKE_GENERATOR_TOOLSET       "")
set(CTEST_BUILD_CONFIGURATION           "$ENV{CMAKE_CONFIG_TYPE}")
set(CTEST_COVERAGE_COMMAND              "/usr/bin/gcov")
set(CTEST_NOTES_FILES                   "${CTEST_SCRIPT_DIRECTORY}/${CTEST_SCRIPT_NAME}")

ctest_start(Experimental)
ctest_configure(BUILD "${CTEST_BINARY_DIRECTORY}" RETURN_VALUE res)
message("build")
ctest_build(BUILD "${CTEST_BINARY_DIRECTORY}" RETURN_VALUE res)
message("test")
ctest_test(BUILD "${CTEST_BINARY_DIRECTORY}" PARALLEL_LEVEL 20 RETURN_VALUE res)
message("done")
