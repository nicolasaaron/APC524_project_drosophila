if(NOT "/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CMakeTests" MATCHES "^/")
  set(slash /)
endif()
set(url "file://${slash}/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CMakeTests/FileDownloadInput.png")
set(dir "/Users/pingwu/APC524_project_drosophila/doxygen/build/cmake-3.13.2/Tests/CMakeTests/downloads")

file(DOWNLOAD
  ${url}
  ${dir}/file3.png
  TIMEOUT 2
  STATUS status
  EXPECTED_HASH SHA1=5555555555555555555555555555555555555555
  )
