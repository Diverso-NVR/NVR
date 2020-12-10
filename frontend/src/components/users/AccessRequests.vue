<template>
  <v-layout align-center justify-center v-resize="onResize">
    <v-flex xs12 sm8 md6>
		<v-layout row wrap style="margin-bottom: 3%">
			<v-flex xs5>
				<v-text-field
					append-icon="search"
					label="E-mail"
					single-line
					hide-details
					@input="filterSearch"
				></v-text-field>
			</v-flex>
		</v-layout>
        <v-data-table
			:items="users"
			class="elevation-4"
			hide-actions hide-headers
			:loading="loader"
			:search="filters"
			:custom-filter="customFilter">
        <template v-slot:items="props">
          <td>
            <div>
              <h3 class="subheading">{{props.item.email}}</h3>
              <div>{{ props.item.role }}</div>
            </div>
          </td>
          <td class="text-xs-center">
            <div v-if="isLarge">
              <v-btn icon color="success" @click="grantAccess(props.item)">
                <v-icon>verified_user</v-icon>
              </v-btn>
              <v-btn icon color="error" @click="deleteUser(props.item)">
                <v-icon>block</v-icon>
              </v-btn>
            </div>
            <div v-else>
              <v-btn color="success" depressed @click="grantAccess(props.item)">Подтвердить</v-btn>
              <v-btn color="error" depressed @click="deleteUser(props.item)">Отклонить</v-btn>
            </div>
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info">Нет новых запросов на доступ</v-alert>
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
      },
      isLarge: false
    };
  },
  computed: mapState({
    users: state =>
      state.users.filter(
        user => user.email_verified === true && user.access === false
      ),
    loader() {
      return this.$store.getters.loading;
    }
  }),
  methods: {
	customFilter(items, filters, filter, headers) {
        // Init the filter class.
        const cf = new this.$MultiFilters(items, filters, filter, headers);

        cf.registerFilter('search', function (searchWord, items) {
          if (searchWord.trim() === '') return items;

          return items.filter(item => {
            return item.email.toLowerCase().includes(searchWord.toLowerCase());
          }, searchWord);

        });

        // Its time to run all created filters.
        // Will be executed in the order thay were defined.
        return cf.runFilters();
    },


    filterSearch(val) {
		this.filters = this.$MultiFilters.updateFilters(this.filters, {search: val});
    },
	
    onResize() {
      this.isLarge = window.innerWidth < 1521;
    },
    grantAccess(user) {
      this.$store.dispatch("emitGrantAccess", { user });
    },
    deleteUser(user) {
      this.$store.dispatch("emitDeleteUser", { user });
    }
  }
};
</script>
