#ifndef HDTV_ROOTEXT_UTIL_COMPAT_HH
#define HDTV_ROOTEXT_UTIL_COMPAT_HH

#include <memory>
#include <type_traits>

namespace HDTV {
namespace Util {

#if __cplusplus >= 201402L

using std::make_unique;

#else

namespace detail {

template <typename T> struct MakeUniq {
  using single_object = std::unique_ptr<T>;
};

template <typename T> struct MakeUniq<T[]> {
  using array = std::unique_ptr<T[]>;
};

template <typename T, size_t N> struct MakeUniq<T[N]> {
  struct invalid_type {};
};

} // namespace detail

// make_unique for single objects
template <typename T, typename... Args>
inline typename detail::MakeUniq<T>::single_object
make_unique(Args &&... args) {
  return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}

// make_unique for arrays of unknown bound
template <typename T, typename... Args>
inline typename detail::MakeUniq<T>::array
make_unique(size_t n) {
  return std::unique_ptr<T>(new typename std::remove_extent<T>::type[n]);
}

// disable make_unique for arrays of known bounds
template <typename T, typename... Args>
inline typename detail::MakeUniq<T>::invalid_type
make_unique(Args &&... args) = delete;

#endif /* __cplusplus */

} // namespace Util
} // namespace HDTV

#endif /* HDTV_ROOTEXT_UTIL_COMPAT_HH */
