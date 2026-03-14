import { createStore } from 'vuex'

export interface RootState {
  testTags: number[]
}

const store = createStore<RootState>({
  state: {
    testTags: [],
  },
  mutations: {
    setTestTags(state, payload: number[]) {
      state.testTags = payload
    },
  },
  getters: {
    testTags: (state) => state.testTags,
  },
})

export default store
