cmake_minimum_required(VERSION 3.6 FATAL_ERROR)

project(fit LANGUAGES CXX)

set(SOURCES
    EEFitter.cc
    ExpBg.cc
    Fitter.cc
    Integral.cc
    InterpolationBg.cc
    Param.cc
    PolyBg.cc
    TheuerkaufFitter.cc
    Util.cc)

set(HEADERS
    Background.hh
    EEFitter.hh
    ExpBg.hh
    Fitter.hh
    Integral.hh
    InterpolationBg.hh
    Option.hh
    Param.hh
    PolyBg.hh
    TheuerkaufFitter.hh
    Util.hh)

find_package(ROOT REQUIRED COMPONENTS Core Hist)
message(STATUS "ROOT Version ${ROOT_VERSION} found in ${ROOT_root_CMD}")
if(${ROOT_VERSION_MINOR} GREATER_EQUAL 20)
  include(${ROOT_DIR}/RootMacros.cmake)
elseif(${ROOT_VERSION_MINOR} EQUAL 19 AND EXISTS ${ROOT_DIR}/RootMacros.cmake)
  include(${ROOT_DIR}/RootMacros.cmake)
else()
  include(${ROOT_DIR}/modules/RootNewMacros.cmake)
endif()

root_generate_dictionary(
  G__${PROJECT_NAME}
  ${HEADERS}
  LINKDEF
  LinkDef.h)

add_library(${PROJECT_NAME} SHARED ${SOURCES} G__${PROJECT_NAME}.cxx)
add_library(hdtv::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
set_target_properties(
  ${PROJECT_NAME}
  PROPERTIES
    RESOURCE
    "${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}_rdict.pcm"
)
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(
  ${PROJECT_NAME}
  ROOT::Core
  ROOT::Hist
  ROOT::MathMore)

install(
  TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RESOURCE DESTINATION lib)
