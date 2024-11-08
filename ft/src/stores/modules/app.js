import { login as loginApi } from "@/api/login";
import router from "@/router";
import { setTokenTime } from "@/utils/auth";

export default {
  namespaced: true,
  state: () => ({
    token: sessionStorage.getItem("token") || "",
    siderType: true,
    lang: sessionStorage.getItem("lang") || "zh",
  }),
  mutations: {
    setToken(state, token) {
      state.token = token;
      sessionStorage.setItem("token", token);
    },
    changeSiderType(state) {
      state.siderType = !state.siderType;
    },
    changLang(state, lang) {
      state.lang = lang;
      sessionStorage.setItem("lang", lang);
    },
  },
  actions: {
    login({ commit }, userInfo) {
      return new Promise((resolve, reject) => {
        loginApi(userInfo)
          .then((res) => {
            console.log(res);
            commit("setToken", res.token);
            setTokenTime();
            router.replace("/");
            resolve();
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    // 退出
    logout({ commit }) {
      commit("setToken", "");
      sessionStorage.clear();
      router.replace("/login");
    },
  },
};
