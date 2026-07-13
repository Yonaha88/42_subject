/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strncmp.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/23 16:17:45 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:28:47 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_strncmp(const char *str1, const char *str2, size_t n)
{
	size_t	idx;

	idx = 0;
	while (idx < n)
	{
		if (str1[idx] != str2[idx])
			return ((unsigned char)str1[idx] - (unsigned char)str2[idx]);
		if (str1[idx] == '\0')
			break ;
		idx++;
	}
	return (0);
}
