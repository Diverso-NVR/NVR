<template>
<v-layout align-center justify-center v-resize="onResize">
	
    <v-flex xs12 sm8 md6>
		<v-layout row wrap>
			<v-flex xs5>
				<v-text-field
					append-icon="search"
					label="E-mail"
					single-line
					hide-details
					@input="filterSearch"
				></v-text-field>
			</v-flex>
			<v-spacer></v-spacer>
			<v-flex xs5>
				<v-select
					:items="roles"
					label="Role"
					@change="filterAuthor"
				></v-select>
			</v-flex>
		</v-layout>
		<v-data-table
			:headers="headers"
			:items="users"
			class="elevation-4"
			hide-actions
			:loading="loader"
			:custom-sort="customSort"
			:search="filters"
			:custom-filter="customFilter"
		>
        <template v-slot:items="props">
          <td>
            <div class="my-2">
              <h3 class="subheading">{{ props.item.email }}</h3>
              <div>{{ props.item.role }}</div>
              <div
                class="mt-2 time"
                :color="isDarkMode ? '#6a737d' : '#F5F5F5'"
              >
                {{ lastLogin(props.item.last_login) }}
              </div>
            </div>
          </td>
          <td class="text-xs-center">
            <div v-if="isLarge">
              <v-btn icon color="warning" @click="changeRole(props.item)">
                <v-icon>supervisor_account</v-icon>
              </v-btn>
              <v-btn icon color="error" @click="deleteUser(props.item)">
                <v-icon>block</v-icon>
              </v-btn>
            </div>
            <div v-else>
              <v-btn color="warning" depressed @click="changeRole(props.item)"
                >Изменить роль</v-btn
              >
              <v-btn color="error" depressed @click="deleteUser(props.item)"
                >Удалить</v-btn
              >
            </div>
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info"
            >Список пользователей пуст</v-alert
          >
        </template>
		</v-data-table>
    </v-flex>
</v-layout>
</template>

<script>
import { mapState } from "vuex";
export default {
  data() {
    return {
	   filters: {
        search: '',
        added_by: '',
      },
	  roles: ["","admin","user","editor"],
      isLarge: false,
      options: {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      },
	  headers: [{text: 'Users', value: 'Users'}]
    };
  },
  computed: mapState({
    users: (state) =>
      state.users.filter(
        (user) =>
          user.access === true &&
          user.email !== state.user.email &&
          user.role !== "superadmin"
      ),
    loader() {
      return this.$store.getters.loading;
    },
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
  }),
  methods: {
	customSort(items, index, isDesc) {
		if (index === "Users") {
			items.sort((a, b) => {
				if (!isDesc) {
					return a.email < b.email ? -1 : 1;
				} else {
					return b.email < a.email ? -1 : 1;
				}
			});
		}
		return items;
	},
	
	customFilter(items, filters, filter, headers) {
        // Init the filter class.
        const cf = new this.$MultiFilters(items, filters, filter, headers);

        cf.registerFilter('search', function (searchWord, items) {
          if (searchWord.trim() === '') return items;

          return items.filter(item => {
            return item.email.toLowerCase().includes(searchWord.toLowerCase());
          }, searchWord);

        });


        cf.registerFilter('added_by', function (added_by, items) {
          if (added_by.trim() === '') return items;

          return items.filter(item => {
            return item.role.toLowerCase() === added_by.toLowerCase();
          }, added_by);

        });

        // Its time to run all created filters.
        // Will be executed in the order thay were defined.
        return cf.runFilters();
    },


    filterSearch(val) {
		this.filters = this.$MultiFilters.updateFilters(this.filters, {search: val});
    },

    filterAuthor(val) {
		this.filters = this.$MultiFilters.updateFilters(this.filters, {added_by: val});
    },

    onResize() {
      this.isLarge = window.innerWidth < 1521;
    },
    changeRole(user) {
      if (user.role === "user") user.role = "editor";
      else if (user.role === "editor") user.role = "admin";
      else user.role = "user";
      this.$store.dispatch("emitChangeRole", { user });
    },
    deleteUser(user) {
      if (confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        this.$store.dispatch("emitDeleteUser", { user });
      }
    },
    lastLogin(timestamp) {
      let postDate = new Date(timestamp);
      return postDate.toLocaleString("ru", this.options);
    },
  },
};
</script>

<style scoped>
.time {
  font-weight: 400;
  font-size: 12px;
}
</style>